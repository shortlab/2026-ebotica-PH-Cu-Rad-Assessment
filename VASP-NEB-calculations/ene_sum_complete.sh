#!/bin/bash
#
# Usage: ./check_jobs.sh /path/to/folder /path/to/script1 /path/to/script2

root_folder="$1"
SCRIPT1="$2"
SCRIPT2="$3"
output_file="$(basename "$root_folder")_results.txt"

#module load python
#module load vasp-tpc/6.4.2-cpu

# Clear or create output files
> "$output_file"
table_output_file="${output_file%.txt}_summary_table.txt"
echo -e "Root_folder\tNeighbor\tSubfolder\tMEB_type\tMEB[eV]\tFWHM[Angstrom]\tJump_dist[Angstrom]\ta_fcc [m]\tV_2atoms [m^3]" \
     > "$table_output_file"

for i in {10..14}; do
  folder="$root_folder/$i"
  [ -d "$folder" ] || continue

  for subsub in "$folder"/*; do
    [ -d "$subsub" ] || continue

    outcar="$subsub/02/OUTCAR"
    if ! [ -f "$outcar" ] || ! grep -q "General timing and accounting informations for this job" "$outcar"; then
      echo "$subsub: job incomplete or OUTCAR missing" >> "$output_file"
      continue
    fi

    cd "$subsub" || continue
    if ! [ -x "$SCRIPT1" ] || ! [ -x "$SCRIPT2" ]; then
      echo "$subsub: scripts missing or not executable" >> "$output_file"
      cd "$OLDPWD"
      continue
    fi

    # Run analysis scripts
    "$SCRIPT1"
    "$SCRIPT2"

    if ! [ -f spline.dat ]; then
      echo "$subsub: spline.dat missing" >> "$output_file"
      cd "$OLDPWD"
      continue
    fi

    # Extract x and y
    mapfile -t x < <(awk 'NF>=3{print $2}' spline.dat)
    mapfile -t y < <(awk 'NF>=3{print $3}' spline.dat)
    jump_dist=$(awk 'NF>=2{val=$2} END{print val}' spline.dat)

    y_first=${y[0]}; y_last=${y[-1]}
    y_max=$y_first
    for v in "${y[@]}"; do
      if (( $(echo "$v > $y_max" | bc -l) )); then y_max=$v; fi
    done
    meb1=$(echo "$y_max - $y_first" | bc -l)
    meb2=$(echo "$y_max - $y_last"  | bc -l)

    # Compute FWHM via Python
    x_str="${x[*]}"; y_str="${y[*]}"
    fwhm=$(python3 - << EOF
import numpy as np
x = np.array("$x_str".split(), dtype=float)
y = np.array("$y_str".split(), dtype=float)
def calculate_fwhm2(x, y):
    half_max = np.max(y) / 2.0

    indices = np.where(y >= half_max)[0]

    if len(indices) < 2:
        return 0.0

    left_idx = indices[0]
    right_idx = indices[-1]

    def interpolate(x0, y0, x1, y1, y_half):
        return x0 + (y_half - y0) * (x1 - x0) / (y1 - y0)

    if left_idx == 0:
        x_left = x[0]
    else:
        x_left = interpolate(x[left_idx-1], y[left_idx-1], x[left_idx], y[left_idx], half_max)

    if right_idx == len(x) - 1:
        x_right = x[-1]
    else:
        x_right = interpolate(x[right_idx], y[right_idx], x[right_idx+1], y[right_idx+1], half_max)

    return x_right - x_left

print(calculate_fwhm2(x, y))
EOF
)
    meb1=$(printf "%.6f" "$meb1")
    meb2=$(printf "%.6f" "$meb2")
    fwhm=$(printf "%.6f" "$fwhm")

    #  New part: read POSCAR and compute a_fcc & V2atoms
    poscar="02/POSCAR"
    #  Read the 3 lattice vectors
read -r x1 y1 z1 <<< "$(sed -n '3p' 02/POSCAR)"
read -r x2 y2 z2 <<< "$(sed -n '4p' 02/POSCAR)"
read -r x3 y3 z3 <<< "$(sed -n '5p' 02/POSCAR)"

#  Compute afcc_m and V2 in one go via Python 
eval "$(python3 <<EOF
import math

# parse the Bash expanded coords
x1,y1,z1 = map(float, "$x1 $y1 $z1".split())
x2,y2,z2 = map(float, "$x2 $y2 $z2".split())
x3,y3,z3 = map(float, "$x3 $y3 $z3".split())

# vector lengths
L1 = math.hypot(x1, y1, z1)
L2 = math.hypot(x2, y2, z2)
L3 = math.hypot(x3, y3, z3)
Lavg = (L1 + L2 + L3) / 3.0

# lattice constant (Å → m)
a_fcc_ang = Lavg / (2 * math.sqrt(2))
a_fcc_m   = a_fcc_ang * 1e-10

# volume of two atoms
r  = a_fcc_m / math.sqrt(2)
V2 = math.pi/3 * r**3

# emit valid Bash assignments:
print(f"afcc_m={a_fcc_m:.12e}")
print(f"V2={V2:.12e}")
EOF
)"

#  Now you have $afcc_m and $V2 in Bash
printf "   a_fcc = %s m\n  V2    = %s m^3\n" "$afcc_m" "$V2"

    neighbor=$(basename "$subsub")
    root_label=$(basename "$root_folder")
    sub_label="$i"

    # Write two rows (for MEB1 and MEB2)
    echo -e "$root_label\t$neighbor\t$sub_label\tMEB1\t$meb1\t$fwhm\t$jump_dist\t$afcc_m\t$V2" >> "$OLDPWD/$table_output_file"
    echo -e "$root_label\t$neighbor\t$sub_label\tMEB2\t$meb2\t$fwhm\t$jump_dist\t$afcc_m\t$V2" >> "$OLDPWD/$table_output_file"

    cd "$OLDPWD"
  done
done

echo "Done. Summary written to $table_output_file"

