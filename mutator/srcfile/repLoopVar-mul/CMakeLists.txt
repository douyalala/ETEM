set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repLoopVar-mul
  repLoopVar-mul.cpp
  )
target_link_libraries(repLoopVar-mul
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