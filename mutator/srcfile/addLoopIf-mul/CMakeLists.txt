set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addLoopIf-mul
  addLoopIf-mul.cpp
  )
target_link_libraries(addLoopIf-mul
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