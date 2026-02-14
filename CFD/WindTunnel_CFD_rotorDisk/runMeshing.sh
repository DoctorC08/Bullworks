#!/bin/bash
#------------------------------------------------------------------------------
# OpenFOAM Automated Meshing Script
# Runs: blockMesh -> surfaceFeatureExtract -> snappyHexMesh -> 
#       decomposePar -> parallel snappyHexMesh -> reconstructPar -> topoSet
#------------------------------------------------------------------------------

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}"
}

# Function to check if command succeeded
check_success() {
    if [ $? -eq 0 ]; then
        print_success "$1 completed successfully"
    else
        print_error "$1 failed"
        exit 1
    fi
}

# Parse command line arguments
PARALLEL=false
NPROCS=4
OVERWRITE=true
SKIP_BLOCK=false
SKIP_FEATURES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -parallel)
            PARALLEL=true
            shift
            ;;
        -np)
            NPROCS="$2"
            shift 2
            ;;
        -no-overwrite)
            OVERWRITE=false
            shift
            ;;
        -skip-block)
            SKIP_BLOCK=true
            shift
            ;;
        -skip-features)
            SKIP_FEATURES=true
            shift
            ;;
        -h|--help)
            echo "Usage: ./runMeshing.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -parallel          Run snappyHexMesh in parallel"
            echo "  -np N              Number of processors (default: 4)"
            echo "  -no-overwrite      Don't use -overwrite flag for snappyHexMesh"
            echo "  -skip-block        Skip blockMesh step"
            echo "  -skip-features     Skip surfaceFeatureExtract step"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./runMeshing.sh                    # Serial execution"
            echo "  ./runMeshing.sh -parallel -np 8    # Parallel with 8 cores"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

# Start timestamp
START_TIME=$(date +%s)
print_header "OpenFOAM Meshing Workflow Started"
echo "Date: $(date)"
if [ "$PARALLEL" = true ]; then
    echo "Mode: Parallel (${NPROCS} processors)"
else
    echo "Mode: Serial"
fi
echo ""

#------------------------------------------------------------------------------
# Step 1: Clean old mesh (optional - commented out for safety)
#------------------------------------------------------------------------------
# print_header "Cleaning Old Mesh"
# rm -rf constant/polyMesh
# rm -rf processor*
# rm -rf postProcessing
# print_success "Old mesh cleaned"
# echo ""

#------------------------------------------------------------------------------
# Step 2: blockMesh
#------------------------------------------------------------------------------
if [ "$SKIP_BLOCK" = false ]; then
    print_header "Step 1: Running blockMesh"
    blockMesh > log.blockMesh 2>&1
    check_success "blockMesh"
    echo "  Log file: log.blockMesh"
    echo ""
else
    print_warning "Skipping blockMesh (using existing mesh)"
    echo ""
fi

#------------------------------------------------------------------------------
# Step 3: surfaceFeatureExtract
#------------------------------------------------------------------------------
if [ "$SKIP_FEATURES" = false ]; then
    print_header "Step 2: Running surfaceFeatureExtract"
    surfaceFeatureExtract > log.surfaceFeatureExtract 2>&1
    check_success "surfaceFeatureExtract"
    echo "  Log file: log.surfaceFeatureExtract"
    echo ""
else
    print_warning "Skipping surfaceFeatureExtract (using existing features)"
    echo ""
fi

#------------------------------------------------------------------------------
# Step 4: snappyHexMesh (Serial or Parallel)
#------------------------------------------------------------------------------
if [ "$PARALLEL" = true ]; then
    #--------------------------------------------------------------------------
    # Parallel execution
    #--------------------------------------------------------------------------
    print_header "Step 3a: Running decomposePar"
    decomposePar > log.decomposePar 2>&1
    check_success "decomposePar"
    echo "  Mesh decomposed into ${NPROCS} domains"
    echo "  Log file: log.decomposePar"
    echo ""

    print_header "Step 3b: Running snappyHexMesh (Parallel)"
    if [ "$OVERWRITE" = true ]; then
        mpirun -np ${NPROCS} snappyHexMesh -parallel -overwrite > log.snappyHexMesh 2>&1
    else
        mpirun -np ${NPROCS} snappyHexMesh -parallel > log.snappyHexMesh 2>&1
    fi
    check_success "snappyHexMesh (parallel)"
    echo "  Log file: log.snappyHexMesh"
    echo ""

    print_header "Step 3c: Running reconstructPar"
    if [ "$OVERWRITE" = true ]; then
        reconstructPar -constant > log.reconstructPar 2>&1
    else
        reconstructPar -latestTime > log.reconstructPar 2>&1
    fi
    check_success "reconstructPar"
    echo "  Log file: log.reconstructPar"
    echo ""

    # Optional: Clean processor directories
    print_warning "Processor directories still exist. To remove them, run: rm -rf processor*"
    echo ""
else
    #--------------------------------------------------------------------------
    # Serial execution
    #--------------------------------------------------------------------------
    print_header "Step 3: Running snappyHexMesh (Serial)"
    if [ "$OVERWRITE" = true ]; then
        snappyHexMesh -overwrite > log.snappyHexMesh 2>&1
    else
        snappyHexMesh > log.snappyHexMesh 2>&1
    fi
    check_success "snappyHexMesh (serial)"
    echo "  Log file: log.snappyHexMesh"
    echo ""
fi

#------------------------------------------------------------------------------
# Step 5: topoSet (Create cell zones)
#------------------------------------------------------------------------------
print_header "Step 4: Running topoSet"
topoSet > log.topoSet 2>&1
check_success "topoSet"
echo "  Log file: log.topoSet"
echo ""

#------------------------------------------------------------------------------
# Summary
#------------------------------------------------------------------------------
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

print_header "Meshing Complete!"
echo "Total time: ${MINUTES}m ${SECONDS}s"
echo ""
echo "Next steps:"
echo "  1. Check mesh quality: checkMesh > log.checkMesh"
echo "  2. Visualize in ParaView: paraFoam"
echo "  3. Verify cell zones exist: foamListTimes -withZones"
echo ""

# Check for mesh quality issues
print_header "Quick Mesh Check"
checkMesh -latestTime > log.checkMesh 2>&1
if grep -q "Failed" log.checkMesh; then
    print_warning "Mesh quality issues detected! Check log.checkMesh"
elif grep -q "OK" log.checkMesh; then
    print_success "Mesh quality check passed!"
else
    print_warning "Unable to determine mesh quality. Check log.checkMesh"
fi
echo "  Log file: log.checkMesh"
echo ""

print_success "All meshing operations completed successfully!"

#------------------------------------------------------------------------------
# End of script
#------------------------------------------------------------------------------