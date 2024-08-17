set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repBinaryOp-sel
  repBinaryOp-sel.cpp
  )
target_link_libraries(repBinaryOp-sel
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