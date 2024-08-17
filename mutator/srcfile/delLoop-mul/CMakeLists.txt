set(LLVM_LINK_COMPONENTS support)

add_clang_executable(delLoop-mul
  delLoop-mul.cpp
  )
target_link_libraries(delLoop-mul
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