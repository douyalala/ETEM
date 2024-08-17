set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repRemUnaryOp-mul
  repRemUnaryOp-mul.cpp
  )
target_link_libraries(repRemUnaryOp-mul
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