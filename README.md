# Bullworks

This is a collection of files for Bullworks engineering club and contains openFOAM computational fluid dynamics (CFD) setups for plane and wind tunnels designed in this club. 

## OpenFoam Workflow
1) Open up CFD Directory and run ```./openfoam-docker```, open appropriate case dir

2) If needed run ```touch [name].foam``` 

3) Prep stl + para.foam
    - Make sure object you want to run CFD on is stl and in  constant/trisurface
    - Scale stl into correct units with ```surfaceConvert in.stl out.stl -clean -scale 0.001```
    - Import stl into paraview along with para.foam
    - Scale para.foam by changing values in blockMeshDict s.t. the stl fits inside of para.foam
    - Modify para.foam surfaces in blockMeshDict s.t. inlet, outlet, and walls are correctly positioned. 

4) Setup snappyHexMeshDict: 
    - Define geometry (create names, ensure refinement box contains stl)
    - Add location in Mesh s.t. it's in the airflow space
    - Optional: run ```surfaceFeatureExtract``` 

5) Run ```snappyHexMesh```

6) Setup 0, constant, and system directory 
  
7) Run CFD: ```simpleFoam```
   Optional: ```renumberMesh -overwrite``` (running before will boost performance)

### Running OpenFoam on multiple cores
1)  Edit decomposeParDict 
    - Set numberOfSumdomains equal to the number of cores you want used. 
    - Run ```decomposePar```
2) Run ```mpirun -np [insert num cores] [solver] -parallel```
3) Run ```reconstructPar```
