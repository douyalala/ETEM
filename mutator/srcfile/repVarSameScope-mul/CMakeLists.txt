set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repVarSameScope-mul
  repVarSameScope-mul.cpp
  )
target_link_libraries(repVarSameScope-mul
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