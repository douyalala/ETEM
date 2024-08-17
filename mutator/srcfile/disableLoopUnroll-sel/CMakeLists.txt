set(LLVM_LINK_COMPONENTS support)

add_clang_executable(disableLoopUnroll-sel
  disableLoopUnroll-sel.cpp
  )
target_link_libraries(disableLoopUnroll-sel
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