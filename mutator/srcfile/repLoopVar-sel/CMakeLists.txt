set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repLoopVar-sel
  repLoopVar-sel.cpp
  )
target_link_libraries(repLoopVar-sel
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