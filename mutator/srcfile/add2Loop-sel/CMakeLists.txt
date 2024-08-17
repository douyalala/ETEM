set(LLVM_LINK_COMPONENTS support)

add_clang_executable(add2Loop-sel
  add2Loop-sel.cpp
  )
target_link_libraries(add2Loop-sel
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