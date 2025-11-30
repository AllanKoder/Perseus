/*
 * Some example C++ code
 *
 * @pdoc
 * id: cpp_example
 * title: C++ Example Block
 * description: |
 *   An example documentation block inside a C-style comment. Lines start with
 *   a leading '*', which should be stripped by Perseus' language helper.
 * code: true
 * @endp
 */

#include <iostream>

// A simple example function referenced by the pdoc block
void example_function() {
    std::cout << "Hello from C++ example" << std::endl;
}
