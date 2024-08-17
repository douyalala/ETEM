set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addFuncArg-sel
  addFuncArg-sel.cpp
  )
target_link_libraries(addFuncArg-sel
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