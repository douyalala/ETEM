set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repIfCond-mul
  repIfCond-mul.cpp
  )
target_link_libraries(repIfCond-mul
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