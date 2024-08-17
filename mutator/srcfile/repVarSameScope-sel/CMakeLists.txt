set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repVarSameScope-sel
  repVarSameScope-sel.cpp
  )
target_link_libraries(repVarSameScope-sel
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