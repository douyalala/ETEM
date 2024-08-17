set(LLVM_LINK_COMPONENTS support)

add_clang_executable(addQualifier-sel
  addQualifier-sel.cpp
  )
target_link_libraries(addQualifier-sel
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