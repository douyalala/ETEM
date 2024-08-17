set(LLVM_LINK_COMPONENTS support)

add_clang_executable(add2If-sel
  add2If-sel.cpp
  )
target_link_libraries(add2If-sel
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