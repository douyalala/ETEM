set(LLVM_LINK_COMPONENTS support)

add_clang_executable(delIf-sel
  delIf-sel.cpp
  )
target_link_libraries(delIf-sel
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