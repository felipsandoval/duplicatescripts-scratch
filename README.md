Duplicate Scripts: ANÁLISIS DE CLONADO Y ABSTRACCIÓN EN SCRATCH
=============
<br>

Según se ha podido comprobar en la literatura científica, los proyectos de Scratch hacen uso extensivo del clonado (i.e., copia y pega) Esto puede suponer una imitación a la hora de desarrollar habilidades como la abstracción, ya que hay elementos, como las definiciones de bloques, que son mucho mejores. Esta herramiente tiene como finalidad la extracción de datos de código en proyectos de Scratch para analizar su duplicidad intra-sprite y project-wide. 

Dado el archivo JSON dentro de los formatos de archivo de Scratch (.SB3) el objetivo es elegir y recopilar los atributos relevantes de cada Sprite, procesar esta información con un algoritmo de clustering, y dar una retroalimentación estadística e informativa tanto de la duplicidad intra-sprite como a nivel de proyecto.

Esta herramienta está desarrollada a partir del código de David Roldán, disponible en el repositorio: https://github.com/davidrol6/duplicatescripts-scratch

### USO

python3 program.py <fichero(.SB3 o .JSON o .ZIP)> [-i]

-i (OPCIONAL): Ignora los opcodes de bloques especificados en IgnoreBlocks.tx. También se ignoran las marcas de control: END_LOOP, END_IF y END_ELSE_IF.

Duplicate Scripts: CLONE AND ABSTRACTION ANALYSIS ON SCRATCH PROJECTS
=============
<br>

As evidenced in the scientific literature, Scratch projects do extensive use of duplication (i.e. copy and paste). This can be a limitation in developing skills such as abstraction, as there are elements, like block definitions, that are much better.

This program aims to extract data from Scratch projects to analyze its duplicity across the code, intra-sprite and project-wide. 

Given the JSON file within Scratch file formats (.SB3), the goal is to choose and collect the relevant attributes of each Sprite, process this information with a clustering algorithm, and give statistical and informative feedback on both intra-sprite and project-level duplicity.

This code takes inspiration by David Roldán works: https://github.com/davidrol6/duplicatescripts-scratch

### USAGE

python3 program.py <file(.SB3 or .JSON or .ZIP)> [-i]

-i (OPTIONAL): Ignores blocks opcodes specified in IgnoreBlocks.txt. Also ignores the control marks: END_LOOP, END_IF y END_ELSE_IF.
