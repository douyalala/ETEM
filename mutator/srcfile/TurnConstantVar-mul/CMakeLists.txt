set(LLVM_LINK_COMPONENTS support)

add_clang_executable(TurnConstantVar-mul
  TurnConstantVar-mul.cpp
  )
target_link_libraries(TurnConstantVar-mul
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