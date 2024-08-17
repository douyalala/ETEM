set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repIfCond-sel
  repIfCond-sel.cpp
  )
target_link_libraries(repIfCond-sel
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