set(LLVM_LINK_COMPONENTS support)

add_clang_executable(optOff-mul
  optOff-mul.cpp
  )
target_link_libraries(optOff-mul
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