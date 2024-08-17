set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repBinaryExpr-mul
  repBinaryExpr-mul.cpp
  )
target_link_libraries(repBinaryExpr-mul
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