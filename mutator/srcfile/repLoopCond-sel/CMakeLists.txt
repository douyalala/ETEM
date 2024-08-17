set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repLoopCond-sel
  repLoopCond-sel.cpp
  )
target_link_libraries(repLoopCond-sel
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