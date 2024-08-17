set(LLVM_LINK_COMPONENTS support)

add_clang_executable(delLoop-sel
  delLoop-sel.cpp
  )
target_link_libraries(delLoop-sel
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