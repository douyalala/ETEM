set(LLVM_LINK_COMPONENTS support)

add_clang_executable(mutator-pos
  ASTScoreTool.cpp
  )
target_link_libraries(mutator-pos
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