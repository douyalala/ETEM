set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addRepModifier-mul
  addRepModifier-mul.cpp
  )
target_link_libraries(addRepModifier-mul
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