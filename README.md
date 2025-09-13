# Bullworks

## To Run IBF CFD
1) Open up CFD Directory and run ```./openfoam-docker```

2) Run ```touch para.foam``` (or some other name.foam)

3) Prep stl + para.foam
    - Make sure object you want to run CFD on is an ascii stl
    - Scale stl into correct units with ```surfaceConvert in.stl out.stl -clean -scale 0.001```
    - Import stl into paraview along with para.foam
    - Scale para.foam by changing values in blockMeshDict s.t. the stl fits inside of para.foam
    - Modify para.foam surfaces in blockMeshDict s.t. inlet, outlet, and walls are correctly positioned. 

4) Setup snappyHexMeshDict: 
    - Define geometry (create names, ensure refinement box contains stl)
    - Add location in Mesh s.t. it's in the airflow space
    - Edit any other parameters as necessary

5) Edit decomposeParDict 
    - Set numberOfSumdomains equal to the number of cores you want used. 
    - Run ```decomposePar```

6) Run ```mpirun -np (insert num cores) snappyHexMesh -parallel```

7) Setup 0 directory (according to Gemini)
    - U (Velocity): For an external aerodynamics problem, the object's surface is usually a noSlip wall, meaning the fluid velocity at the surface is zero. The inlet is typically a fixedValue with a uniform velocity vector (e.g., (26.82 0 0) for a 60 mph flow). The outlet can be inletOutlet or zeroGradient.
    - p (Pressure): For an incompressible flow, you set a reference pressure. The inlet is often a zeroGradient, while the outlet is a fixedValue of 0. 
    - Turbulence Fields: For a turbulent flow (which is typical for external aerodynamics), you need to set up files for your chosen turbulence model, such as k (turbulent kinetic energy) and epsilon or omega (dissipation rate or specific dissipation rate, respectively). These fields also require appropriate boundary conditions at the inlet and outlet.

8) Setup constant directory (according to Gemini)
    - transportProperties: Specifies the fluid's kinematic viscosity (nu). For air at standard conditions, this is approximately 1.5*10^(-5) m^2/s.
    - turbulenceProperties: Determines which turbulence model to use for the simulation. A common choice for external aerodynamics is the kOmegaSST model. You would specify simulationType as RAS and RASModel as kOmegaSST here.

9) Setup system directory (according to Gemini)
    - controlDict: This is the main control file. You define:
        - application: The solver you will use (e.g., simpleFoam for a steady-state incompressible flow).
        - startTime: The starting time of the simulation (usually 0).
        - endTime: The total simulation time.
        - deltaT: The time step size.
        - writeControl: How often results are written to disk.
    - fvSchemes: Here you specify the numerical schemes for discretizing the equations. This can get complex, but for many cases, the default schemes in a template tutorial are a good starting point. You will specify schemes for terms like gradSchemes, divSchemes, and laplacianSchemes.
    - fvSolution: This file sets the numerical solvers and their tolerances for each field (p, U, etc.). It also contains settings for the pressure-velocity coupling algorithm, such as SIMPLE.

10) Run CFD
    - To run CFD on single core use: ```simpleFoam```
    - For multiple cores follow same idea as before: 
    ```decomposePar``` 
    ```mpirun --allow-run-as-root -np (num cores) simpleFoam -parallel```