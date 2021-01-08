pipeline {
    agent {
        label 'cicd-slave'
    }

    stages {
        stage('test') {
            steps {
                sh '''
                    . /etc/profile
                    make copy
                    make test
                '''
            }
        }
    }
}
