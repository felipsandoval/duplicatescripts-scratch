Duplicate Scripts: Análisis de proyectos en Scratch
=============
<br>
El programa tienen como finalidad analizar y extraer datos relativos a los duplicidad de código en los proyectos de Scratch. 

Dado el archivo JSON dentro de los formatos de archivo de Scratch (.SB3) el objetivo es elegir y recopilar los atributos relevantes de cada Sprite, procesar esta información con un algoritmo de clustering, y dar una retroalimentación estadística e informativa tanto de la duplicidad intra-sprite como a nivel de proyecto.

<br>

### USO

python3 program.py <fichero(.SB3 o .JSON o .ZIP)> [-i]

-i (OPCIONAL): Ignora los opcodes de bloques especificados en IgnoreBlocks.txt

Duplicate Scripts: For project analysis on Scratch
=============
<br>
Scripts are applied to analyze and extract data regarding duplicates scripts on Scratch projects. 

Given the JSON file within Scratch file formats (.SB3) the objective is to choose and collect relevant attributes of each Sprite, process this information with a clustering algorithm, and give insight feedback with duplicity both intra-sprite and project-wide.
<br>


### USAGE

python3 program.py <file(.SB3 or .JSON or .ZIP)> [-i]

-i (OPTIONAL): Ignore blocks opcodes within IgnoreBlocks.txt
