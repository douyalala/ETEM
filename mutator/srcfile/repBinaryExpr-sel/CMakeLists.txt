set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repBinaryExpr-sel
  repBinaryExpr-sel.cpp
  )
target_link_libraries(repBinaryExpr-sel
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