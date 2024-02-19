# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import re  # To get the variant name after (+)

import spack.build_systems.cmake
import spack.build_systems.makefile
from spack.package import *


def find_model_flag(str):
    res = re.findall(r"\+(\w+)", str)
    if not res:
        return ""
    return res


class Babelstream(CMakePackage, CudaPackage, ROCmPackage, MakefilePackage):
    """Measure memory transfer rates to/from global device memory on GPUs.
    This benchmark is similar in spirit, and based on, the STREAM benchmark for CPUs."""

    homepage = "https://github.com/UoB-HPC/BabelStream"
    url = "https://github.com/UoB-HPC/BabelStream/archive/refs/tags/v5.0.tar.gz"
    git = "https://github.com/UoB-HPC/BabelStream.git"
    version("5.0", sha256="1a418203fbfd95595bdc66047e2e39d8f1bba95a49725c9ecb907caf1af2521f")
    version("4.0", sha256="a9cd39277fb15d977d468435eb9b894f79f468233f0131509aa540ffda4f5953")
    version("3.4", sha256="e34ee9d5ccdead019e3ea478333bcb7886117d600e5da8579a626f6ee34209cf")
    version("3.3", sha256="4c89c805b277d52776feeb7a8eef7985a0d9295ce3e0bb2333bf715f724723cf")
    version("3.2", sha256="20309b27ddd09ea37406bcc6f46fd32e9372bf3d145757e55938d19d69cdc49d")
    version("3.1", sha256="be69e6085e8966e12aa2df897eea6254b172e5adfa03de0adbb89bc3065f4fbe")
    version("3.0", sha256="776219c72e0fdc36f134e6975b68c7ab25f38206f8f8af84a6f9630648c24800")
    version("1.0", sha256="3cfb9e45601f1f249878355c72baa6e6a61f6c811f8716d60b83c7fb544e1d5c")
    # version("main", branch="main")
    maintainers("tomdeakin", "kaanolgu", "tom91136")
    # Previous maintainers: "robj0nes"
    build_system("cmake", "makefile", default="cmake")
    # Languages
    # Also supported variants are cuda and rocm (for HIP)
    variant("sycl", default=False, description="Enable SYCL support")
    variant("sycl2020", default=False, description="Enable SYCL support")
    variant("omp", default=False, description="Enable OpenMP support")
    variant("ocl", default=False, description="Enable OpenCL support")
    variant("tbb", default=False, description="Enable TBB support")
    variant("acc", default=False, description="Enable OpenACC support")
    variant("hip", default=False, description="Enable HIP support")
    variant("thrust", default=False, description="Enable THRUST support")
    variant("raja", default=False, description="Enable RAJA support")
    variant("std", default=False, description="Enable STD support")

    # Some models need to have the programming model abstraction downloaded -
    # this variant enables a path to be provided.
    variant("dir", values=str, default="none", description="Enable Directory support") 
    variant("sycl_submodel", values=("usm", "acc"), when="+sycl2020", default="usm", description="SYCL2020 -> choose between usm and acc methods")
    variant("std_submodel", values=("data", "indices","ranges"), when="+std", default="data", description="STD -> choose between data, indices and ranges models")

    sycl_compiler_implementations = ["oneapi-icpx","oneapi-clang","dpcpp","hipsycl","computecpp"]  # list them here, with the default first
    sycl_compiler_implementations_description = "Compile using the specified SYCL compiler implementation\
           Supported values are \
           ONEAPI-ICPX  - icpx as a standalone compiler \
           ONEAPI-Clang - oneAPI's Clang driver (enabled via `source /opt/intel/oneapi/setvars.sh  --include-intel-llvm`)\
           DPCPP        - dpc++ as a standalone compiler (https://github.com/intel/llvm)\
           HIPSYCL      - hipSYCL compiler (https://github.com/illuhad/hipSYCL)s\
           COMPUTECPP   - ComputeCpp compiler (https://developer.codeplay.com/products/computecpp/ce/home)"
    variant("sycl_compiler_implementation", values=sycl_compiler_implementations, default=sycl_compiler_implementations[0], when="+sycl", description=sycl_compiler_implementations_description)
    variant("sycl_compiler_implementation", values=sycl_compiler_implementations, default=sycl_compiler_implementations[0], when="+sycl2020", description=sycl_compiler_implementations_description)
    
    
    variant("thrust_backend", values=("cuda", "rocm"), default="cuda", when="+thrust", description="Which THRUST implementation to use, supported options include option= \
            - CUDA (via https://github.com/NVIDIA/thrust)\
            - ROCM (via https://github.com/ROCmSoftwarePlatform/rocThrust)")

    # Kokkos conflict and variant
    conflicts(
        "dir=none", when="+kokkos", msg="KOKKKOS requires architecture to be specfied by dir="
    )
    variant("kokkos", default=False, description="Enable KOKKOS support")

    # ACC conflict
    variant("cpu_arch", values=str, default="none", description="Enable CPU Target for ACC and OMP")

    # STD conflicts
    conflicts("+std", when="%gcc@:10.1.0", msg="STD requires newer version of GCC")

    # CUDA conflict
    conflicts(
        "cuda_arch=none",
        when="+cuda",
        msg="CUDA requires architecture to be specfied by cuda_arch=",
    )
    variant("mem", values=str, default="DEFAULT", description="Enable MEM Target for CUDA")
    # Raja offload
    variant(
        "raja_offload",
        values=("cpu", "nvidia"),
        default="cpu",
        when="+raja",
        description="Enable RAJA Target [CPU or NVIDIA] / Offload with custom settings for OpenMP",
    )
    #std-* offload
    variant(
        "std_offload",
        values=("nvhpc","none"),
        default="none",
        when="+std",
        description="Enable offloading support (via the non-standard `-stdpar`) for the new NVHPC SDK",
    )
    variant(
        "std_onedpl_backend",
        values=("openmp","tbb","dpcpp","none"),
        default="none",
        when="+std",
        description="Implements policies using OpenMP,TBB or dpc++",
    )
    variant(
        "std_use_tbb",
        values=(True,False),
        default=False,
        when="+std",
        description="No-op if ONE_TBB_DIR is set. Link against an in-tree oneTBB via FetchContent_Declare, see top level CMakeLists.txt for details"
    )
    variant(
        "std_use_onedpl",
        values=(True,False),
        default=False,
        when="+std",
        description="Link oneDPL which implements C++17 executor policies (via execution_policy_tag) for different backends"
    )


    # download raja from https://github.com/LLNL/RAJA
    conflicts(
        "dir=none",
        when="+raja",
        msg="RAJA implementation requires architecture to be specfied by dir=",
    )
    # depends_on("cuda@12.3.0:", when="+thrust")
    # Thrust Conflict
    # conflicts("~cuda", when="+thrust", msg="Thrust requires +cuda variant")
    depends_on("thrust", when="+thrust")
    depends_on("cuda", when="+thrust")
    depends_on("hip", when="+hip")
    depends_on("rocthrust", when="+thrust thrust_backend=rocm")
    depends_on("intel-tbb", when="+std +std_use_tbb")
    depends_on("intel-oneapi-dpl", when="+std +std_use_onedpl")
    depends_on("intel-tbb", when="+std +std_use_onedpl")
    # TBB Dependency
    depends_on("intel-tbb", when="+tbb")
    partitioner_vals = ["auto", "affinity", "static", "simple"]
    variant(
        "partitioner",
        values=partitioner_vals,
        default="auto",
        description="Partitioner specifies how a loop template should partition its work among threads.\
            Possible values are:\
            AUTO     - Optimize range subdivision based on work-stealing events.\
            AFFINITY - Proportional splitting that optimizes for cache affinity.\
            STATIC   - Distribute work uniformly with no additional load balancing.\
            SIMPLE   - Recursively split its range until it cannot be further subdivided.\
            See https://spec.oneapi.com/versions/latest/elements/oneTBB/source/algorithms.html#partitioners for more details.",
    )

    # Kokkos Dependency
    depends_on("kokkos@3.7.1", when="+kokkos")

    # OpenCL Dependency

    backends = {
        "ocl": [
            ("amd", "rocm-opencl", "enable ROCM backend"),
            ("cuda", "cuda", "enable Cuda backend"),
            ("intel", "intel-oneapi-compilers", "enable Intel backend"),
            ("pocl", "pocl@1.5", "enable POCL backend"),
        ],
        "kokkos": [
            ("cuda", "cuda", "enable Cuda backend"),
            ("omp", "none", "enable Cuda backend"),
        ],
    }
    backend_vals = ["none"]
    for lang in backends:
        for item in backends[lang]:
            backend, dpdncy, descr = item
            backend_vals.append(backend.lower())

    variant("backend", values=backend_vals, default="none", description="Enable backend support")

    for lang in backends:
        for item in backends[lang]:
            backend, dpdncy, descr = item
            if dpdncy.lower() != "none":
                depends_on("%s" % dpdncy.lower(), when="backend=%s" % backend.lower())
    # this flag could be used in all required languages
    variant("flags", values=str, default="none", description="Additional CXX flags to be provided")

    # CMake specific dependency
    with when("build_system=cmake"):
        depends_on("cmake@3.14.0:", type="build")

    # This applies to all

    depends_on("opencl-c-headers", when="+ocl")


    with when("build_system=makefile"):
        implementation_vals = [
            "DoConcurrent",
            "Array",
            "OpenMP",
            "OpenMPWorkshare",
            "OpenMPTarget",
            "OpenMPTargetLoop",
            "OpenMPTaskloop",
            "OpenACC",
            "OpenACCArray",
            "CUDA",
            "CUDAKernel",
            "Sequential",
        ]
        variant(
            "foption", values=implementation_vals, default="Sequential", description="Implementation"
        )
        # The fortran Makefile is inside the src/fortran so we need to address this
        build_directory = "src/fortran"
        # build_directory = '.'
        build_name = ""

        variant(
            "test", values=str, default="none", description="Test Variant for debugging purposes"
        )

class CMakeBuilder(spack.build_systems.cmake.CMakeBuilder):
    def cmake_args(self):
        model_list = ["sycl","sycl2020","omp","cuda","ocl","tbb","acc","hip","thrust","raja","std"]
        # convert spec to string to work on it
        spec_string = str(self.spec)
        
        # take only the first portion of the spec until space
        spec_string_truncate = spec_string.split(" ", 1)[0]
        truncated_model_list = find_model_flag(spec_string_truncate)  # Prints out ['cuda', 'thrust']
        # Filter out elements from truncated_model_list list that are not in model_list list
        filtered_model_list = [item for item in truncated_model_list if item in model_list]
        # for +acc and +thrust the CudaPackage appends +cuda variant too so we need to filter cuda from list
        # e.g. we choose 'thrust' from the list of ['cuda', 'thrust']
        if len(filtered_model_list) > 1:
            filtered_model_list = [elem for elem in filtered_model_list if (elem != "cuda" and elem!="rocm")]
            if "std" in filtered_model_list[0]:
                args = ["-DMODEL=" + "std-" + self.spec.variants["std_submodel"].value]
            else:
                args = ["-DMODEL=" + filtered_model_list[0]]
        else:
            # do some alterations here to append sub models too
            if "std" in filtered_model_list[0]:
                args = ["-DMODEL=" + "std-" + self.spec.variants["std_submodel"].value]
            elif "sycl2020" in filtered_model_list[0]:
                args = ["-DMODEL=" + "sycl2020-" + self.spec.variants["sycl_submodel"].value]
                print(args)
            elif "rocm" in filtered_model_list[0]:
                args = ["-DMODEL=hip"]
            else:
                args = ["-DMODEL=" + filtered_model_list[0]]
        if (filtered_model_list[0] != "tbb" and filtered_model_list[0] != "thrust"):
            args.append("-DCMAKE_CXX_COMPILER=" + spack_cxx)
        print(spec_string)

        # ===================================
        #             ACC
        # ===================================
        """
        register_flag_optional(TARGET_DEVICE
        "[PGI/NVHPC only] This sets the `-target` flag, possible values are:
             gpu       - Globally set the target device to an NVIDIA GPU
             multicore - Globally set the target device to the host CPU
         Refer to `nvc++ --help` for the full list"
         register_flag_optional(CUDA_ARCH
        "[PGI/NVHPC only] Only applicable if `TARGET_DEVICE` is set to `gpu`.
         Nvidia architecture in ccXY format, for example, sm_70 becomes cc70,
         will be passed in via `-gpu=` (e.g `cc70`)
         Possible values are:
             cc35  - Compile for compute capability 3.5
             cc50  - Compile for compute capability 5.0
             cc60  - Compile for compute capability 6.0
             cc62  - Compile for compute capability 6.2
             cc70  - Compile for compute capability 7.0
             cc72  - Compile for compute capability 7.2
             cc75  - Compile for compute capability 7.5
             cc80  - Compile for compute capability 8.0
             ccall - Compile for all supported compute capabilities
         Refer to `nvc++ --help` for the full list"
        "")

register_flag_optional(TARGET_PROCESSOR
        "[PGI/NVHPC only] This sets the `-tp` (target processor) flag, possible values are:
             px          - Generic x86 Processor
             bulldozer   - AMD Bulldozer processor
             piledriver  - AMD Piledriver processor
             zen         - AMD Zen architecture (Epyc, Ryzen)
             zen2        - AMD Zen 2 architecture (Ryzen 2)
             sandybridge - Intel SandyBridge processor
             haswell     - Intel Haswell processor
             knl         - Intel Knights Landing processor
             skylake     - Intel Skylake Xeon processor
             host        - Link native version of HPC SDK cpu math library
             native      - Alias for -tp host
        Refer to `nvc++ --help` for the full list"
        "")
        """
        if self.spec.satisfies("+acc+cuda"):
            if (self.spec.compiler.name == "nvhpc") or (self.spec.compiler.name == "pgi"):
                target_device = "multicore" if self.spec.variants["cpu_arch"].value != "none" else "gpu" if "cuda_arch" in self.spec.variants else None
                if self.spec.variants["cpu_arch"].value != "none":
                    # get the cpu architecture value from user
                    target_processor = self.spec.variants["cpu_arch"].value[0]
                    args.append("-DTARGET_PROCESSOR=" + target_processor)
                    # args.append(
                    #     "-DCXX_EXTRA_FLAGS="
                    #     + "-target="
                    #     + target_device
                    #     + "-tp="
                    #     + target_processor
                    # )
                if "cuda_arch" in self.spec.variants:
                    cuda_arch_list = self.spec.variants["cuda_arch"].value
                    # the architecture value is only number so append cc_ to the name
                    cuda_arch = "cc" + cuda_arch_list[0]
                    # args.append(
                    #     "-DCXX_EXTRA_FLAGS=" + "-target=" + target_device + "-gpu=" + cuda_arch
                    # )
                    args.append("-DCUDA_ARCH=" + cuda_arch)
                args.append("-DTARGET_DEVICE=" + target_device)
        # ===================================
        #    STDdata,STDindices,STDranges
        # ===================================

        if "+std" in self.spec:
            if self.spec.satisfies("+std_use_tbb"):
                args.append("-DCXX_EXTRA_FLAGS=-ltbb")
            if self.spec.satisfies("+std_use_onedpl"):
                # args.append("-DCXX_EXTRA_FLAGS=-ltbb")
                # args.append("-DCXX_EXTRA_FLAGS=-loneDPL")
                args.append("-DUSE_ONEDPL=" + self.spec.variants["std_onedpl_backend"].value.upper())
            if self.spec.variants["std_offload"].value != "none":
                # the architecture value is only number so append cc_ to the name
                cuda_arch = "cc" + self.spec.variants["cuda_arch"].value[0]
                args.append("-DNVHPC_OFFLOAD=" + cuda_arch)


        # ===================================
        #             CUDA
        # ===================================
        if self.spec.satisfies("+cuda~kokkos~acc~omp~thrust"):
            # Set up the cuda macros needed by the build
            cuda_arch_list = self.spec.variants["cuda_arch"].value
            # "-DCUDA_ARCH" requires sm_ 
            # the architecture value is only number so append sm_ to the name
            cuda_arch = "sm_" + cuda_arch_list[0]
            args.append("-DCUDA_ARCH=" + cuda_arch)
            cuda_dir = self.spec["cuda"].prefix
            cuda_comp = cuda_dir + "/bin/nvcc"
            args.append("-DCMAKE_CUDA_COMPILER=" + cuda_comp)
            args.append("-DMEM=" + self.spec.variants["mem"].value.upper())
            if self.spec.variants["flags"].value != "none":
                # append_opts "-DCXX_EXTRA_FLAGS=-march=znver3"
                # CSD3  A100s are hosted on a EPYC 7763
                args.append("-DCUDA_EXTRA_FLAGS=" + self.spec.variants["flags"].value)

        # ===================================
        #             OMP
        # ===================================
        # `~kokkos` option is there to prevent +kokkos +omp setting to use omp directly from here
        # Same applies for raja
        if self.spec.satisfies("+omp~kokkos~raja"):
            args.append("-DCMAKE_C_COMPILER=" + spack_cc)
            if "cuda_arch" in self.spec.variants:
                # the architecture value is only number so append cc_ to the name
                cuda_arch = "cc" + self.spec.variants["cuda_arch"].value[0]
                args.append("-DOFFLOAD=ON")
                args.append("-DOFFLOAD_FLAGS=" + " -mp=gpu;"  + "-gpu=" + cuda_arch)
            elif ("amdgpu_target" in self.spec.variants) and (
                self.spec.variants["amdgpu_target"].value != "none"
            ):
                args.append("-DOFFLOAD=ON")
                args.append("-DOFFLOAD_FLAGS=" + "-fopenmp;--offload-arch=" + self.spec.variants["amdgpu_target"].value[0])
            elif ("cpu_arch" in self.spec.variants) and (
                self.spec.variants["cpu_arch"].value != "none"
            ):
                args.append("-DOFFLOAD=" + "INTEL")
            elif "offload" in self.spec.variants and (
                self.spec.variants["offload"].value != "none"
            ):
                args.append("-DOFFLOAD=" + "ON")
                args.append("-DOFFLOAD_FLAGS=" + self.spec.variants["offload"].value)
            else:
                args.append("-DOFFLOAD=" + "OFF")
                args.append("-DCXX_EXTRA_FLAGS=-MP;-march=" + str( self.spec.target) + ";-Ofast")

        # ===================================
        #            SYCL
        # ===================================

        if "+sycl" in self.spec:
            args.append("-DCXX_EXTRA_FLAGS=" + "-fsycl")
            args.append("-DSYCL_COMPILER=" + self.spec.variants["sycl_compiler_implementation"].value.upper())
            if self.spec.variants["sycl_compiler_implementation"].value.upper() == "none":
                args.append("-DSYCL_COMPILER_DIR=" + self.spec.variants["dir"].value)
            if self.spec.variants["sycl_compiler_implementation"].value.upper() != "ONEAPI-DPCPP":
                args.append(
                    "-DSYCL_COMPILER_DIR=" + self.spec.variants["sycl_compiler_implementation"].value.upper()
                )
            if self.spec.variants["sycl_compiler_implementation"].value.upper() == "COMPUTECPP":
                args.append("-DOpenCL_LIBRARY=")

        # ===================================
        #              SYCL 2020
        # ===================================

        if "+sycl2020" in self.spec:
            if self.spec.satisfies("%oneapi"):
                # -fsycl flag is required for setting up sycl/sycl.hpp seems like
                #  it doesn't get it from the CMake file
                args.append("-DCXX_EXTRA_FLAGS= -fsycl -O3")
                # this is required to enable -DCMAKE_CXX_COMPILER=icpx flag from CMake
                args.append("-DSYCL_COMPILER=ONEAPI-ICPX")
            else:
                args.append(
                    "-DSYCL_COMPILER=" + self.spec.variants["sycl_compiler_implementation"].value.upper()
                )
                if self.spec.variants["sycl_compiler_implementation"].value.upper() != "ONEAPI-DPCPP":
                    args.append(
                        "-DSYCL_COMPILER_DIR=" + self.spec.variants["sycl_compiler_implementation"].value.upper()
                    )
                    if self.spec.variants["sycl_compiler_implementation"].value.upper() == "COMPUTE-CPP":
                        args.append("-DOpenCL_LIBRARY=")

        # ===================================
        #             HIP(ROCM)
        # ===================================

        if "+hip" in self.spec:
            # hip_comp = self.spec["hip"].prefix + "/bin/hipcc"
            # args.append("-DCMAKE_CXX_COMPILER=" + hip_comp)
            args.append(
                "-DCXX_EXTRA_FLAGS= --offload-arch="
                + str(self.spec.variants["amdgpu_target"].value[0])
                + str(self.spec.variants["flags"].value)
                + str(" -O3")
            )

        # ===================================
        #             TBB
        # ===================================

        if "+tbb" in self.spec:
            args.append("-DONE_TBB_DIR=" + self.spec["intel-tbb"].prefix + "/tbb/latest/")
            args.append("-DPARTITIONER=" + self.spec.variants["partitioner"].value.upper())
            # "Whether to use std::vector<T> for storage or use aligned_alloc.
            # C++ vectors are *zero* initialised where as aligned_alloc
            #  is uninitialised before first use."
            args.append("-DUSE_VECTOR=" + "OFF")
            args.append("-DUSE_TBB=" + "OFF")

        # ===================================
        #             OpenCL (ocl)
        # ===================================
        if "+ocl" in self.spec:
            if "backend" in self.spec.variants:
                if "cuda" in self.spec.variants["backend"].value:
                    cuda_dir = self.spec["cuda"].prefix
                    args.append("-DOpenCL_LIBRARY=" + cuda_dir + "/lib64/libOpenCL.so")
                elif "amd" in self.spec.variants["backend"].value:
                    rocm_dir = self.spec["rocm-opencl"].prefix
                    args.append("-DOpenCL_LIBRARY=" + rocm_dir + "/lib64/libOpenCL.so")
                elif "intel" in self.spec.variants["backend"].value:
                    intel_lib = (
                        self.spec["intel-oneapi-compilers"].prefix
                        + "/compiler/"
                        + str(self.spec["intel-oneapi-compilers"].version)
                        + "/linux/lib/libOpenCL.so"
                    )
                    args.append("-DOpenCL_LIBRARY=" + intel_lib)
                elif "pocl" in self.spec.variants["backend"].value:
                    pocl_lib = self.spec["pocl"].prefix + "/lib64/libOpenCL.so"
                    args.append("-DOpenCL_LIBRARY=" + pocl_lib)


        # ===================================
        #             RAJA
        # ===================================
        if "+raja" in self.spec:
            args.append("-DRAJA_IN_TREE=" + self.spec.variants["dir"].value)
            if "offload" in self.spec.variants:
                if "nvidia" in self.spec.variants["offload"].value:
                    cuda_dir = self.spec["cuda"].prefix
                    cuda_comp = cuda_dir + "/bin/nvcc"
                    args.append("-DCMAKE_CUDA_COMPILER=" + cuda_comp)
                    args.append("-DTARGET=NVIDIA")
                    cuda_arch_list = self.spec.variants["cuda_arch"].value
                    int_cuda_arch = int(cuda_arch_list[0])
                    cuda_arch = "sm_" + cuda_arch_list[0]
                    args.append("-DCUDA_ARCH=" + cuda_arch)

                    args.append("DCUDA_TOOLKIT_ROOT_DIR=" + self.spec["cuda"].prefix)
                    if self.spec.variants["flags"].value != "none":
                        args.append("-DCUDA_EXTRA_FLAGS=" + self.spec.variants["flags"].value)
                # if("cpu" in self.spec.variants['offload'].value):

            if "omp" in self.spec.variants["backend"].value:
                args.append("-DENABLE_OPENMP=ON")
            if "cuda" in self.spec.variants["backend"].value:
                args.append("-DENABLE_CUDA=ON")

        # ===================================
        #             THRUST
        # ===================================
        if "+thrust" in self.spec:
            if "cuda" in self.spec.variants["thrust_backend"].value:
                args.append("-DTHRUST_IMPL=" + self.spec.variants["thrust_backend"].value.upper())
                args.append("-SDK_DIR=" + self.spec["thrust"].prefix + "/include")
                cuda_arch_list = self.spec.variants["cuda_arch"].value
                # this model uses CMAKE_CUDA_ARCHITECTURES which only requires number of cuda_arch
                # no need to append sm_ or cc_
                cuda_arch = cuda_arch_list[0]
                args.append("-DCUDA_ARCH=" + cuda_arch)
                cuda_dir = self.spec["cuda"].prefix
                cuda_comp = cuda_dir + "/bin/nvcc"
                # args.append("-DCMAKE_CUDA_COMPILER=" + join_path(self.spec["cuda"].prefix.bin, "nvcc"))
                # args.append("-DCMAKE_CUDA_COMPILER=" + spack_cc)
                args.append("-DCMAKE_CUDA_COMPILER=" + cuda_comp)
                args.append("-DCMAKE_CUDA_FLAGS=-ccbin " + spack_cc) 
                args.append("-DBACKEND=" + self.spec.variants["backend"].value.upper())
                if self.spec.variants["flags"].value != "none":
                    args.append("-DCUDA_EXTRA_FLAGS=" + self.spec.variants["flags"].value)
                # args.append("-DCXX_EXTRA_FLAGS=-MP;-march=skylake-avx512;-Ofast")


            if "rocm" in self.spec.variants["thrust_backend"].value:
                env["SPACK_CXX"] = self.spec["hip"].hipcc
                args.append("-DTHRUST_IMPL=" + self.spec.variants["thrust_backend"].value.upper())
                args.append("-SDK_DIR=" + self.spec["rocthrust"].prefix)
                args.append("-DBACKEND=" + self.spec.variants["backend"].value.upper())

        # ===================================
        #             kokkos
        # ===================================
        # kokkos implementation is versatile and it could use cuda or omp architectures as backend
        # The usage should be spack install babelstream +kokkos backend=[cuda or omp or none]
        if "+kokkos" in self.spec:
            args.append("-DKOKKOS_IN_TREE=" + self.spec.variants["dir"].value)
            # args.append("-DKOKKOS_IN_PACKAGE=" + self.spec["kokkos"].prefix)
            if "backend" in self.spec.variants:
                if "cuda" in self.spec.variants["backend"].value:
                    args.append("-DKokkos_ENABLE_CUDA=ON")
                    cuda_arch_list = self.spec.variants["cuda_arch"].value
                    int_cuda_arch = int(cuda_arch_list[0])
                    # arhitecture kepler optimisations
                    if int_cuda_arch in (30, 32, 35, 37):
                        args.append("-D" + "Kokkos_ARCH_KEPLER" + str(int_cuda_arch) + "=ON")
                    # arhitecture maxwell optimisations
                    if int_cuda_arch in (50, 52, 53):
                        args.append("-D" + "Kokkos_ARCH_MAXWELL" + str(int_cuda_arch) + "=ON")
                    # arhitecture pascal optimisations
                    if int_cuda_arch in (60, 61):
                        args.append("-D" + "Kokkos_ARCH_PASCAL" + str(int_cuda_arch) + "=ON")
                    # architecture volta optimisations
                    if int_cuda_arch in (70, 72):
                        args.append("-D" + "Kokkos_ARCH_VOLTA" + str(int_cuda_arch) + "=ON")
                    if int_cuda_arch == 75:
                        args.append("-DKokkos_ARCH_TURING75=ON")
                if "omp" in self.spec.variants["backend"].value:
                    args.append("-DKokkos_ENABLE_OPENMP=ON")

        # not in ["kokkos", "raja", "acc", "hip"] then compiler forced true
        if set(model_list).intersection(["kokkos", "raja", "acc", "hip"]) is True:
            args.append("-DCMAKE_CXX_COMPILER_FORCED=True")

        return args


class MakefileBuilder(spack.build_systems.makefile.MakefileBuilder):
    build_directory = "src/fortran"

    # Generate Compiler Specific includes
    def edit(self, pkg, spec, prefix):
        config = {
            "FC": pkg.compiler.fc_names[0],
            "FCFLAGS": "",
            "ARCH": spec.target.family,
            "DOCONCURRENT_FLAG": "",
            "ARRAY_FLAG": "",
            "OPENMP_FLAG": "",
            "OPENACC_FLAG": "",
            "CUDA_FLAG": "",
            "SEQUENTIAL_FLAG": "",
        }
        # Dictionary mapping compiler names to unsupported options
        unsupported_options = {
            "arm": ["CUDA", "CUDAKernels", "OpenACC", "OpenACCArray"],
            "aocc" : ["CUDA", "CUDAKernels"],
            "cce" : ["CUDA", "CUDAKernels"],
            "gcc" : ["CUDA"],
            "nvhpc" :  ["OpenMPTaskloop"],
            "oneapi": ["CUDA","CUDAKernels","OpenACC","OpenACCArray"],
            "fj" : ["CUDA", "CUDAKernels", "OpenACC"]
        }

        # Check if spec.compiler.name is in the unsupported_options dictionary
        unsupported_value = self.spec.variants["foption"].value
        compiler_name = spec.compiler.name
        unsupported = any(unsupported_value in options for options in unsupported_options.get(compiler_name, []))

        if unsupported:
            raise InstallError(f"{unsupported_value} is not supported by the {compiler_name} compiler")
        # ===================================
        #               ARM
        # ===================================
        if spec.compiler.name == "arm":
            flags = "-std=f2018 " + pkg.compiler.opt_flags[4] + " -Wall -Wno-unused-variable"
            flags += "-march=" + str(spec.target)

            config["DOCONCURRENT_FLAG"] = pkg.compiler.openmp_flag  # libomp.so required
            config["ARRAY_FLAG"] = pkg.compiler.openmp_flag  # libomp.so required
            config["OPENMP_FLAG"] = pkg.compiler.openmp_flag  # libomp.so required
            config["OPENACC_FLAG"] = "-fopenacc"



        # ===================================
        #               AMD
        # ===================================
        if spec.compiler.name == "aocc":
            flags = (
                "-std=f2018 "
                + pkg.compiler.opt_flags[3]
                + " -Wall -Wno-unused-variable"
            )

            config["DOCONCURRENT_FLAG"] = pkg.compiler.openmp_flag  # libomp.so required
            config["ARRAY_FLAG"] = pkg.compiler.openmp_flag  # libomp.so required
            config["OPENMP_FLAG"] = pkg.compiler.openmp_flag  # libomp.so required
            config["OPENACC_FLAG"] = "-fopenacc"


        # ===================================
        #               CRAY
        # ===================================
        if spec.compiler.name == "cce":
            flags = "-e F -O3"

            config["DOCONCURRENT_FLAG"] = "-h thread_do_concurrent -DCRAY_THREAD_DOCONCURRENT"
            config["ARRAY_FLAG"] = "-h autothread"
            config[
                "OPENMP_FLAG"
            ] = pkg.compiler.openmp_flag  # if clang based it will be -fopenmp else -h omp
            config["OPENACC_FLAG"] = "-h acc"  # for cpu only -h omp


        # ===================================
        #               GCC
        # ===================================
        if spec.compiler.name == "gcc":
            flags = "-std=f2018 -O3 "
            flags += "-Wall -Wno-unused-dummy-argument -Wno-unused-variable "
            flags += "-march=" + str(spec.target)

            config["FCFLAGS"] = flags
            config["DOCONCURRENT_FLAG"] = "-ftree-parallelize-loops=4"
            config["OPENMP_FLAG"] = pkg.compiler.openmp_flag
            config["OPENACC_FLAG"] = "-fopenacc"


        # ===================================
        #               NVHPC
        # ===================================
        if spec.compiler.name == "nvhpc":
            flags = pkg.compiler.opt_flags[4]  # for -O3
            # FCFLAGS	:= -O3 -Minform=inform -Minfo=all
            flags += " -Minform=warn "
            TARGET = "gpu"  # target = "multicore"
            config["TARGET"] = TARGET
            if "cuda_arch" in self.spec.variants:
                cuda_arch_list = self.spec.variants["cuda_arch"].value
                # the architecture value is only number so append sm_ to the name
                cuda_arch = "cc" + cuda_arch_list[0]
            # config['MARCH'] = "neoverse-v1,neoverse-n1,icelake-server,znver3,cortex-a78ae"
            GPUFLAG = " -gpu=" + cuda_arch        
            flags += "-tp=" + str(spec.target)   
            # this is to allow apples-to-apples comparison with DC in non-DC GPU impls
            # set exactly one of these pairs!
            # MANAGED = "-DUSE_MANAGED -gpu=managed"
            # DEVICE=""
            # ------------
            DEVICE = ("-DUSE_DEVICE -cuda -gpu=nomanaged",)
            MANAGED = ""
            config["FCFLAGS"] = flags
            config["DOCONCURRENT_FLAG"] = GPUFLAG + " -stdpar=" + TARGET + " " + DEVICE
            config["ARRAY_FLAG"] = GPUFLAG + " -stdpar=" + TARGET + " " + MANAGED
            config["OPENMP_FLAG"] = GPUFLAG + " -mp=" + TARGET + " " + MANAGED
            config["OPENACC_FLAG"] = GPUFLAG + " -acc=" + TARGET + " " + MANAGED
            config["CUDA_FLAG"] = GPUFLAG + " -cuda -acc=gpu" + " " + MANAGED

        # ===================================
        #               ONEAPI
        # ===================================
        if spec.compiler.name == "oneapi":
            flags = "-std18 -Ofast -xHOST -qopt-zmm-usage=low"
            if config["FC"] == "ifort":
                flags += "-qopt-streaming-stores=always"

            config["DOCONCURRENT_FLAG"] = "-qopenmp" + (
                "-parallel" if config["FC"] == "ifort" else ""
            )
            config["ARRAY_FLAG"] = "-qopenmp" + ("-parallel" if config["FC"] == "ifort" else "")
            config["OPENMP_FLAG"] = "-qopenmp" + (
                "-fopenmp-targets=spir64 -DUSE_FLOAT=1" if config["FC"] == "ifx" else ""
            )


        # ===================================
        #               FJ
        # ===================================
        if spec.compiler.name == "fj":
            flags = "-X08 -Kfast -KA64FX -KSVE -KARMV8_3_A -Kzfill=100 "
            flags += "-Kprefetch_sequential=soft "
            flags += "-Kprefetch_line=8 -Kprefetch_line_L2=16 -Koptmsg=2 "
            # FJ Fortran system_clock is low resolution
            flags += "-Keval -DUSE_OMP_GET_WTIME=1 "

            config["DOCONCURRENT_FLAG"] = "-Kparallel,reduction -DNOTSHARED"
            config["ARRAY_FLAG"] = "-Kparallel,reduction"
            config["OPENMP_FLAG"] = pkg.compiler.openmp_flag

        with open(self.build_directory + "/make.inc." + spec.compiler.name, "w+") as inc:
            for key in config:
                inc.write("{0} = {1}\n".format(key, config[key]))

    def setup_build_environment(self, env):
        ######################################
        # Build and Installation Directories #
        ######################################

        # The environment variable ESMF_DIR must be set to the full pathname
        # of the top level ESMF directory before building the framework.
        env.set("COMPILER", self.spec.compiler.name)
        env.set("IMPLEMENTATION", self.spec.variants["foption"].value)
        # DEBUG
        # print(self.spec.variants["foption"].value)
        # print(self.spec.compiler.version)
        # print(platform.machine())
        # This creates a testing tree (if one doesn't already exist) and
        # copies the binaries from `src/fortran` to `SpackPackage/bin`.
        # This allows you to use the testing tree independently of the
        # source tree in the future.
        # print(pkg.compiler.cc_pic_flag)

    @property
    def build_name(self):
        compiler_prefix = self.spec.compiler.name
        implementation_prefix = self.spec.variants["foption"].value
        return "{}.{}.{}".format("BabelStream", compiler_prefix, implementation_prefix)

    def install(self, pkg, spec, prefix):
        mkdir(prefix.bin)
        install(self.build_directory + "/" + self.build_name, prefix.bin)
        # To check the make.inc file generated
        install_tree(self.build_directory, prefix.lib)