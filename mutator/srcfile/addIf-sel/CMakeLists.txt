set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addIf-sel
  addIf-sel.cpp
  )
target_link_libraries(addIf-sel
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