set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repBinaryOp-mul
  repBinaryOp-mul.cpp
  )
target_link_libraries(repBinaryOp-mul
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