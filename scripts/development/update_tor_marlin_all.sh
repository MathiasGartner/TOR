scripts=(
marlin_32.sh
marlin_2.sh
marlin_18.sh
marlin_5.sh
marlin_1.sh
marlin_3.sh
marlin_4.sh
marlin_6.sh
marlin_7.sh
marlin_8.sh
marlin_9.sh
marlin_10.sh
marlin_11.sh
marlin_12.sh
marlin_13.sh
marlin_14.sh
marlin_15.sh
marlin_16.sh
marlin_17.sh
marlin_19.sh
marlin_20.sh
marlin_21.sh
marlin_22.sh
marlin_23.sh
marlin_24.sh
marlin_25.sh
marlin_26.sh
marlin_27.sh
marlin_28.sh
marlin_29.sh
marlin_30.sh
)
for script in "${scripts[@]}"; do
bash "$script" &
done
wait
echo "done"
