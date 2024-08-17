set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addVarDecl-sel
  addVarDecl-sel.cpp
  )
target_link_libraries(addVarDecl-sel
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