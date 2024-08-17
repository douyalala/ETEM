set(LLVM_LINK_COMPONENTS support)

add_clang_executable(TurnConstantVar-sel
  TurnConstantVar-sel.cpp
  )
target_link_libraries(TurnConstantVar-sel
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