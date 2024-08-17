set(LLVM_LINK_COMPONENTS support)

add_clang_executable(add2Loop-mul
  add2Loop-mul.cpp
  )
target_link_libraries(add2Loop-mul
  PRIVATE
  clangAST
  clangASTMatchers
  clangBasic
  clangFrontend
  clangSerialization
  clangTooling
  clangDriver
  clangRewrite
  clangRewriteFrontend
  clangStaticAnalyzerFrontend
  clangToolingSyntax
  )