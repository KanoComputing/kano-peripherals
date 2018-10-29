#
# conanfile.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Specifies the touch-detect package for Conan
#


from conans import ConanFile, CMake


class TouchdetectConan(ConanFile):
    name = "touch-detect"
    version = "4.2.0"
    license = "<Put the package license here>"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Touchdetect here>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    exports_sources = "src/*", "lib/*", "include/*", "CMakeLists.txt"

    def build(self):
        cmake = CMake(self)
        cmake.configure(source_folder="")
        cmake.build()

    def package(self):
        self.copy("*.h", dst="include", src="include")
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.dylib*", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["touch_detect"]

    def deploy(self):
        self.copy("*.h")
        self.copy("*.lib")
        self.copy("*.dll")
        self.copy("*.dylib*")
        self.copy("*.so")
        self.copy("*.a")
