set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addRepModifier-sel
  addRepModifier-sel.cpp
  )
target_link_libraries(addRepModifier-sel
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