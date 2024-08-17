set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addVarDecl-mul
  addVarDecl-mul.cpp
  )
target_link_libraries(addVarDecl-mul
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