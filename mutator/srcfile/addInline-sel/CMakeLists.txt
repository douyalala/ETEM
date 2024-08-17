set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addInline-sel
  addInline-sel.cpp
  )
target_link_libraries(addInline-sel
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