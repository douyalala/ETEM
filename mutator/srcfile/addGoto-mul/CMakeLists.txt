set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addGoto-mul
  addGoto-mul.cpp
  )
target_link_libraries(addGoto-mul
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