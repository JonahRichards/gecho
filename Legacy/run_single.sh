module load maxwell python/3.10

echo "Generating geometries..."

python3 pre.py

echo "Executing ECHO2D..."

./ECHO2D

echo "Executing Post Processing."

python3 post.py
python3 gif.py

echo "Finished."