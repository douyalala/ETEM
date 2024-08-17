set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repIntConstant-mul
  repIntConstant-mul.cpp
  )
target_link_libraries(repIntConstant-mul
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