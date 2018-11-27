import os
import shutil

from conans import CMake, ConanFile, tools


class GrpcConan(ConanFile):
    name = "grpc"
    version = "1.13.0"
    license = "MIT"
    url = "https://github.com/AtaLuZiK/conan-grpc"
    description = "gRPC is a modern, open source, high-performance remote procedure call (RPC) framework that can run anywhere."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "use_proto_lite": [True, False],
    }
    default_options = "shared=False", "use_proto_lite=False"
    exports_sources = ["gRPCConfig.cmake.in"]
    generators = "cmake"
    requires = (
        "zlib/1.2.11@conan/stable",
        "c-ares/1.14.0@conan/stable",
        "OpenSSL/1.0.2n@conan/stable",
        "gflags/2.2.1@bincrafters/stable",
        "protobuf/3.5.1@zimmerk/stable",
    )

    @property
    def zip_folder_name(self):
        return "%s-%s" % (self.name, self.version)

    def source(self):
        zip_name = "%s.tar.gz" % self.version
        tools.download("https://github.com/grpc/grpc/archive/v%s" % zip_name, zip_name)
        tools.check_md5(zip_name, "c6fc06d80ffd9c2ab903764bf69f4606")
        tools.unzip(zip_name)
        os.unlink(zip_name)
        with tools.chdir(self.zip_folder_name):
            tools.replace_in_file("CMakeLists.txt", "project(${PACKAGE_NAME} C CXX)", 
                '''project(${PACKAGE_NAME} C CXX)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')
            tools.replace_in_file("CMakeLists.txt", "include(cmake/benchmark.cmake)", "")
            tools.replace_in_file("CMakeLists.txt", "add_executable(check_epollexclusive", "add_executable(check_epollexclusive EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_executable(gen_hpack_tables", "add_executable(gen_hpack_tables EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_executable(gen_legal_metadata_characters", "add_executable(gen_legal_metadata_characters EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_executable(gen_percent_encoding_tables", "add_executable(gen_percent_encoding_tables EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_create_jwt", "add_executable(grpc_create_jwt EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_print_google_default_creds_token", "add_executable(grpc_print_google_default_creds_token EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_verify_jwt", "add_executable(grpc_verify_jwt EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_library(grpc_csharp_ext SHARED", "add_library(grpc_csharp_ext SHARED EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_csharp_plugin", "add_executable(grpc_csharp_plugin EXCLUDE_FROM_ALL")
            # tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_node_plugin", "add_executable(grpc_node_plugin EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_objective_c_plugin", "add_executable(grpc_objective_c_plugin EXCLUDE_FROM_ALL")
            # tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_php_plugin", "add_executable(grpc_php_plugin EXCLUDE_FROM_ALL")
            # tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_python_plugin", "add_executable(grpc_python_plugin EXCLUDE_FROM_ALL")
            # tools.replace_in_file("CMakeLists.txt", "add_executable(grpc_ruby_plugin", "add_executable(grpc_ruby_plugin EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "add_library(grpc_csharp_ext SHARED", "add_library(grpc_csharp_ext SHARED EXCLUDE_FROM_ALL")
            tools.replace_in_file("CMakeLists.txt", "install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/etc/roots.pem", '''export(TARGETS %s NAMESPACE gRPC:: FILE gRPCTargets.cmake)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/etc/roots.pem''' % ' '.join([
    'address_sorting', 'gpr',
    'grpc', 'grpc_cronet', 'grpc_unsecure', 
    'grpc++', 'grpc++_cronet', 'grpc++_error_details', 'grpc++_reflection', 'grpc++_unsecure', 'grpc_plugin_support',
    'grpc_cpp_plugin',
    'grpc_node_plugin', 'grpc_php_plugin', 'grpc_python_plugin', 'grpc_ruby_plugin',
]))

    def build(self):
        shutil.move("gRPCConfig.cmake.in", "%s/cmake/gRPCConfig.cmake.in" % self.zip_folder_name)
        cmake = CMake(self)
        cmake.definitions["gRPC_ZLIB_PROVIDER"] = "package"
        cmake.definitions["gRPC_CARES_PROVIDER"] = "package"
        cmake.definitions["gRPC_SSL_PROVIDER"] = "package"
        cmake.definitions["gRPC_PROTOBUF_PROVIDER"] = "package"
        cmake.definitions["gRPC_PROTOBUF_PACKAGE_TYPE"] = "CONFIG"
        cmake.definitions["gRPC_GFLAGS_PROVIDER"] = "package"
        cmake.definitions["gRPC_USE_PROTO_LITE"] = "ON" if self.options.use_proto_lite else "OFF"
        cmake.definitions["gRPC_INSTALL"] = "OFF"
        cmake.configure(source_folder=self.zip_folder_name)
        cmake.build()

    def package(self):
        libs = ["gpr", "grpc", "grpc_cronet", "grpc_unsecure", "grpc++*"]
        for name in libs:
            self.copy("%s.lib" % name, dst="lib", src="lib", keep_path=False)
            self.copy("lib%s.so*" % name, dst="lib", src="lib", keep_path=False)
            self.copy("lib%s.a" % name, dst="lib", src="lib", keep_path=False)
            self.copy("lib%s.dylib" % name, dst="lib", src="lib", keep_path=False)
        if self.settings.os == "Windows":
            self.copy("*.exe", dst="bin", src="bin")
        else:
            self.copy("*", dst="bin", src="bin")
        self.copy("*.h", dst="include", src="%s/include" % self.zip_folder_name)
        self.copy("gRPCConfig.cmake", dst="cmake")
        self.copy("gRPCConfigVersion.cmake", dst="cmake")

    def package_info(self):
        self.cpp_info.libs = ["grpc", "grpc++", "libprotobuf"]
