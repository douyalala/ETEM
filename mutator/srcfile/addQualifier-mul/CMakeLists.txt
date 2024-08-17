set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addQualifier-mul
  addQualifier-mul.cpp
  )
target_link_libraries(addQualifier-mul
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