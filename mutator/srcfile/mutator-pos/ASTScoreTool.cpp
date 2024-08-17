//------------------------------------------------------------------------------
// add/init AST nodes' score
// usage: mutator-pos <path to main.c> -- <path to score file> AST_ID (or init)
//------------------------------------------------------------------------------
#include <sstream>
#include <string>
#include <iostream>
#include <fstream>
#include <memory>
#include <map>
#include <typeinfo>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/Support/raw_ostream.h"
using namespace std;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory VisitAST_Category("usage: mutator-pos <path to main.c> -- <path to score file> AST_ID (or init)");
static string score_file = "";
static string mode = "";
static int64_t tar_AST_ID;
static ifstream in; 
static ofstream out; 
static map<int64_t,double> node_score;
#define DECAY 0

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  void visitAncestorStmt() {
    double add_point=1;
    while (!ancestor_nodes.empty()) {
      int64_t ancestor = ancestor_nodes.top();
      ancestor_nodes.pop();

      node_score[ancestor]+=add_point;

      add_point*=DECAY;
    }
  }

  bool TraverseStmt(Stmt *S) {
      if(Context==NULL){
        llvm::errs() <<"Error: Context is NULL" << "\n";
        return 0;
      }

      // // debug print
      // cout<<S->getID(*Context)<<"::Stmt"<<endl;
      ancestor_nodes.push(S->getID(*Context));

      // init / add score
      if(mode=="init"){
        node_score[S->getID(*Context)]=1;
      }else{
        if(S->getID(*Context)==tar_AST_ID){
          visitAncestorStmt();
          return 0;
        }
      }

      bool result = RecursiveASTVisitor::TraverseStmt(S);

      ancestor_nodes.pop();
      return result;
  }

  bool TraverseDecl(Decl *D) {
      if(Context==NULL){
        llvm::errs() <<"Error: Context is NULL" << "\n";
        return 0;
      }

      // // debug print
      // cout<<D->getID()<<"::Decl"<<endl;
      ancestor_nodes.push(D->getID());

      // init / add score
      if(mode=="init"){
        node_score[D->getID()]=1;
      }else{
        if(D->getID()==tar_AST_ID){
          visitAncestorStmt();
          return 0;
        }
      }
      
      bool result = RecursiveASTVisitor::TraverseDecl(D);

      ancestor_nodes.pop();
      return result;
  }

private:
  Rewriter &TheRewriter;
  std::stack<int64_t> ancestor_nodes;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  void HandleTranslationUnit(ASTContext &Context) {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.Context=&Context;
    Visitor.TraverseAST(Context);
  }

private:
  MyASTVisitor Visitor;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}
  
  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  srand( (unsigned)time( NULL ) );
  score_file= argv[3];
  mode = argv[4];

  cout<<"-- running: mutator-pos"<<endl;
  cout<<"---- score_file: "<<score_file<<endl;
  cout<<"---- mode: "<<mode<<endl;
  
  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser=CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());

  if(mode=="init"){ 
    node_score[-1]=1; // for add var decl
  }else{
    tar_AST_ID=atoll(mode.c_str());
    in.open(score_file,ios::in);
    if(in.fail()){     
      llvm::errs() <<"Error: Fail to open the in file."<< "\n";
      in.close();    
      return 0; 
    }
    string in_line;
    while(in>>in_line){
      istringstream iss(in_line);
      string id_str, score_str;
      int64_t id;
      double score;
      getline(iss, id_str, ':');
      getline(iss, score_str);
      id = atoll(id_str.c_str());
      score = atof(score_str.c_str());
      node_score[id]=score;
    }
    in.close();
  }

  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  out.open(score_file,ios::trunc);
  if(out.fail()){     
    llvm::errs() <<"Error: Fail to open the out file." << "\n";
    out.close();
    return 0; 
  }
  for(auto it=node_score.begin();it!=node_score.end();it++){
    out << it->first << ":" << it->second <<endl;
  }

  return 0;
}
