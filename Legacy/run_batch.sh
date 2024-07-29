module load maxwell python/3.10

#echo "Generating geometries..."

#./rpython3 pre.py

echo "Executing ECHO2D..."

run_executable() {
    ./ECHO2D > "log.txt"
    rm -f ./ECHO2D
    python3 ../../post.py
    #python3 ../../gif.py
}

parent_directory="runs"

executable_path="ECHO2D"

subdirectories=$(find "$parent_directory" -maxdepth 1 -mindepth 1 -type d)

for subdirectory in $subdirectories; do
    if ! [ -d "$subdirectory/round" ]; then
        echo "Executing ECHO in $subdirectory..."

        cp "$executable_path" "$subdirectory/"

        (cd "$subdirectory" && run_executable) &
    fi
done

wait

echo "All executables have been launched and completed."

echo "Finished."