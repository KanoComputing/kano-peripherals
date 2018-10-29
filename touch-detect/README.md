# Touch Detect

## Building

Create the build directory

```
mkdir -p build
cd build
```

(Optional) Install dependencies with `conan` (otherwise ensure that you have
the dependencies available to the build system)

```
conan install ..
```

Build

```
cmake ..
make
```

## Conan (Experimental)

This package has been created to be (optionally) shipped with a conan package,
hence you can do an operation like:

```
cd build
conan create .. KanoComputing/stable
```

This can then be pushed to the artifactory and used as a dependency of another
project.

To use this package, make sure that your `conanfile.txt` looks like this

```
[requires]
touch-detect/4.2.0@KanoComputing/stable
```
