set(LLVM_LINK_COMPONENTS support)

add_clang_executable(remModifierQualifier-sel
  remModifierQualifier-sel.cpp
  )
target_link_libraries(remModifierQualifier-sel
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