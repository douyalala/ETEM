set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repRemUnaryOp-sel
  repRemUnaryOp-sel.cpp
  )
target_link_libraries(repRemUnaryOp-sel
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